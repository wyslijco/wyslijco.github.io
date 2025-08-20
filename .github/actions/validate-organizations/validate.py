#!/usr/bin/env python3
"""
Validation script for organization YAML files in GitHub Actions.
Validates organization files for schema compliance and slug conflicts.
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

import click
import yaml
import requests
from krs_puller import KRSDataPuller, KRSMaintenanceError


class OrganizationValidator:
    """Validates organization YAML files for GitHub Actions."""
    
    def __init__(self, organizations_dir: str, slug_field: str):
        self.organizations_dir = Path(organizations_dir)
        self.slug_field = slug_field
        self.reserved_slugs = {
            "info",
            "organizacje", 
            "404"
        }
    
    def load_all_organizations(self) -> Tuple[Dict[str, str], List[str]]:
        """Load all organization files and return slug to filename mapping with errors."""
        slug_to_file = {}
        errors = []
        
        if not self.organizations_dir.exists():
            return slug_to_file, errors
            
        yaml_files = list(self.organizations_dir.glob("*.yaml")) + list(self.organizations_dir.glob("*.yml"))
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and self.slug_field in data:
                        slug = data[self.slug_field]
                        if slug in slug_to_file:
                            errors.append(f"Znaleziono duplikaty pola {self.slug_field} o wartości '{slug}' w plikach: {yaml_file.name} i {slug_to_file[slug]}")
                        else:
                            slug_to_file[slug] = yaml_file.name
            except Exception as e:
                errors.append(f"Błąd wczytywania pliku {yaml_file.name}: {e}")
        
        return slug_to_file, errors
    
    def _validate_krs_data(self, krs: str, data: dict, errors: List[str]) -> None:
        """Validate KRS data against external API and check name match."""
        try:
            krs_data = KRSDataPuller(krs)
            
            if not krs_data.name:
                errors.append(f"KRS {krs} istnieje, ale dane organizacji są niekompletne")
                return
            
            # Check name match
            yaml_name = data.get('nazwa', '').strip()
            krs_name = krs_data.name.strip()
            
            if yaml_name.strip().lower() != krs_name.strip().lower():
                errors.append(f"Niezgodność nazwy organizacji: w YAML jest '{yaml_name}', ale w KRS jest '{krs_name}'")
                
        except KRSMaintenanceError as e:
            print(f"  ⚠️  {e}")
            
        except requests.HTTPError:
            errors.append(f"KRS {krs} nie zostało znalezione w rejestrze lub wystąpił błąd sieci")
    
    def validate_yaml_structure(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Validate YAML file structure and required fields."""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            errors.append(f"Nieprawidłowa składnia YAML: {e}")
            return False, errors
        except Exception as e:
            errors.append(f"Błąd odczytu pliku: {e}")
            return False, errors
        
        if not data:
            errors.append("Pusty plik YAML")
            return False, errors
        
        # Required fields
        required_fields = [
            'nazwa',           # organization name
            self.slug_field,   # URL slug (adres)
            'strona',          # website
            'krs',             # KRS number
            'dostawa',         # delivery info
            'produkty'         # products list
        ]
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Brakuje wymaganego pola: {field}")
        
        # Validate specific field formats
        if 'krs' in data:
            krs = str(data['krs'])
            if not re.fullmatch(r"\d{10}", krs):
                errors.append(f"Nieprawidłowy format KRS: {krs} (oczekiwano 10 cyfr)")
            else:
                # Validate KRS against external API, including name match
                self._validate_krs_data(krs, data, errors)
        
        if self.slug_field in data:
            slug = data[self.slug_field]
            if not isinstance(slug, str) or not slug.strip():
                errors.append(f"Nieprawidłowy {self.slug_field}: musi być niepustym ciągiem znaków")
            elif not re.fullmatch(r"[a-z0-9-]+", slug):
                errors.append(f"Nieprawidłowy format {self.slug_field}: {slug} (dozwolone tylko małe litery, cyfry i myślniki)")
        
        # Validate dostawa structure
        if 'dostawa' in data:
            delivery = data['dostawa']
            if not delivery or not isinstance(delivery, dict):
                errors.append("Pole dostawa musi być obiektem z wymaganymi polami")
            else:
                required_delivery_fields = ['ulica', 'kod', 'miasto', 'telefon']
                for field in required_delivery_fields:
                    if field not in delivery:
                        errors.append(f"Brakuje wymaganego pola dostawy: dostawa.{field}")
                    elif not delivery[field] or not str(delivery[field]).strip():
                        errors.append(f"Pole dostawa.{field} nie może być puste")
                
                # Validate postal code format
                if 'kod' in delivery:
                    postal_code = str(delivery['kod'])
                    if not re.fullmatch(r"\d{2}-\d{3}", postal_code):
                        errors.append(f"Nieprawidłowy format kodu pocztowego: {postal_code} (oczekiwany format: 00-000)")
                
                # Validate phone number
                if 'telefon' in delivery:
                    phone = re.sub(r"[\s-]", "", str(delivery['telefon']))
                    if not re.fullmatch(r"(\+?48|0048)?\d{9}", phone):
                        errors.append(f"Nieprawidłowy format numeru telefonu: {delivery['telefon']}")
        
        # Validate produkty structure
        if 'produkty' in data and data['produkty']:
            if not isinstance(data['produkty'], list):
                errors.append("produkty musi być listą")
            else:
                for i, product in enumerate(data['produkty']):
                    if not isinstance(product, dict):
                        errors.append(f"produkty[{i}] musi być obiektem")
                        continue
                    
                    if 'nazwa' not in product:
                        errors.append(f"produkty[{i}] brakuje wymaganego pola: nazwa")
                    elif not product['nazwa'] or not str(product['nazwa']).strip():
                        errors.append(f"produkty[{i}] pole nazwa nie może być puste")
                    
                    if 'link' not in product:
                        errors.append(f"produkty[{i}] brakuje wymaganego pola: link")
                    elif not product['link'] or not str(product['link']).strip():
                        errors.append(f"produkty[{i}] pole link nie może być puste")
        
        return len(errors) == 0, errors
    
    def validate_slug_conflicts(self, files_to_check: List[str], all_organizations: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Check for slug conflicts with reserved slugs."""
        errors = []
        
        # Check reserved slug conflicts for files being checked
        for slug, filename in all_organizations.items():
            if filename in files_to_check and slug in self.reserved_slugs:
                errors.append(f"Zarezerwowany {self.slug_field} '{slug}' używany w pliku {filename}")
        
        return len(errors) == 0, errors
    
    def validate_files(self, files_to_check: List[str]) -> bool:
        """Validate a list of organization files."""

        print("=================================================")
        print("🚀 Rozpoczynam walidację organizacji...")

        # Load all organizations and check for duplicate slugs
        all_organizations, load_errors = self.load_all_organizations()
        
        if load_errors:
            print("❌ Krytyczne błędy wczytywania organizacji:")
            for error in load_errors:
                print(f"     - {error}")
            print("💥 Walidacja nie powiodła się!")
            return False
        
        print(f"Walidacja {len(files_to_check)} pliku/ów organizacji...")
        print(f"Katalog organizacji: {self.organizations_dir}")
        print(f"Pole {self.slug_field}: {self.slug_field}")
        print(f"Zarezerwowane adresy stron: {', '.join(sorted(self.reserved_slugs))}")
        print()
        
        # Validate individual file structures
        for file_path in files_to_check:
            print(f"Walidacja {file_path}...")
            # file_path already includes organizations/ prefix, so use it directly
            full_path = Path(file_path)
            
            if not full_path.exists():
                print(f"  ❌ Plik nie znaleziony: {file_path}")
                all_valid = False
                continue
            
            is_valid, errors = self.validate_yaml_structure(full_path)
            
            if is_valid:
                print(f"  ✅ Walidacja struktury zakończona pomyślnie")
            else:
                print(f"  ❌ Walidacja struktury nie powiodła się:")
                for error in errors:
                    print(f"     - {error}")
                all_valid = False
        
        print()
        
        # Check slug conflicts
        print("Sprawdzanie konfliktów adresów...")
        is_valid, errors = self.validate_slug_conflicts(files_to_check, all_organizations)
        
        if is_valid:
            print("  ✅ Nie znaleziono konfliktów adresów")
            all_valid = True
        else:
            print("  ❌ Znaleziono konflikty adresów:")
            for error in errors:
                print(f"     - {error}")
            all_valid = False
        
        print()
        
        if all_valid:
            print("🎉 Wszystkie walidacje zakończone pomyślnie!")
        else:
            print("💥 Walidacja nie powiodła się!")

        print("=================================================")
        
        return all_valid


@click.command()
@click.option('--files', required=True, help='Space-separated list of organization YAML files to validate')
@click.option('--organizations-dir', default='organizations', help='Directory containing organization YAML files')
@click.option('--slug-field', default='adres', help='YAML field name for organization slug')
def main(files: str, organizations_dir: str, slug_field: str):
    """Validate organization YAML files."""
    
    # Parse files list
    files_list = [f.strip() for f in files.split() if f.strip()]
    
    if not files_list:
        print("Brak plików do walidacji")
        sys.exit(0)
    
    validator = OrganizationValidator(organizations_dir, slug_field)
    
    if validator.validate_files(files_list):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
