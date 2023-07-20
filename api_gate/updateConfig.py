def is_valid_new_value(value):
    numbers = value.strip().split(';')
    if len(numbers) != 8:
        return False

    for number in numbers:
        try:
            num = int(number)
            if not (0 <= num <= 2000):
                return False
        except ValueError:
            return False

    return True


def update_config_file(config_file, new_values):
    with open(config_file, 'r') as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        key_value = line.strip().split('=')
        if key_value[0].strip() in new_values and is_valid_new_value(new_values[key_value[0].strip()]):
            new_value = new_values[key_value[0].strip()]
            updated_line = f"{key_value[0].strip()} = {new_value}\n"
            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)

    with open(config_file, 'w') as f:
        f.writelines(updated_lines)


if __name__ == "__main__":
    config_file = "api_gate/config_nvdsanalytics2.txt"
    new_values = {
        "line-crossing-car_in": "100;200;300;400;500;600;700;800",
        "line-crossing-person_in": "1700;1800;1900;2000;0;100;2000;1500", # Invalid, will not be replaced
        "line-crossing-person_out": "2500;2600;2700;2800;2900;3000;3100;3200", # Invalid, will not be replaced
    }

    update_config_file(config_file, new_values)
