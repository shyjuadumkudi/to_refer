from itertools import combinations

def find_combinations(nums, target):
    result = []
    for r in range(2, len(nums) + 1):
        for combo in combinations(nums, r):            
            if sum(combo) == target:
                result.append(list(combo))
    return result


if __name__ == '__main__':
    nums = [2, 3, 6, 4, 1, 7]
    target = 7
    print(f"List : {nums}")
    print(f"Target : {target}")
    print(f"\n{find_combinations(nums, target)}")
