from IOmanager import get_best_results
from options import Options
from scheduler import parse_arguments, check_one_instance, check_all_instances

if __name__ == '__main__':
    args_instance, execute_all = parse_arguments()
    program_options = Options()
    best_results = get_best_results(program_options)
    if not execute_all:
        check_one_instance(args_instance, best_results, program_options)
    else:
        check_all_instances(program_options, best_results)
    exit(0)
