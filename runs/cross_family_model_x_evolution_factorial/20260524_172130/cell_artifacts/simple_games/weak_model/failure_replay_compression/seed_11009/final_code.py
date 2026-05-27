def choose_move(observation):
    player = observation.get('player', {})
    current_pos = player.get('pos', (0, 0))
    grid = observation.get('grid', [])
    resources = observation.get('resources', [])
    opponents = observation.get('opponents', [])
    goals = observation.get('goals', [])
    territory = observation.get('territory', [])

    def get_closest(targets, pos):
        min_dist = float('inf')
        target_pt = None
        for t in targets:
            dist = abs(pos[0] - t[0]) + abs(pos[1] - t[1])
            if dist < min_dist:
                min_dist = dist
                target_pt = t
        return target_pt

    def find_nearest(lst, pos):
        return get_closest(lst, pos)

    target_pos = None
    for opp in opponents:
        opp_pos = opp.get('pos')
        if opp_pos:
            dist = abs(current_pos[0] - opp_pos[0]) + abs(current_pos[1] - opp_pos[1])
            if dist <= 3:
                target_pos = opp_pos
                break
    if target_pos is None:
        if resources:
            target_pos = find_nearest(resources, current_pos)
        elif goals:
            target_pos = get_closest(goals, current_pos)
        elif territory:
            target_pos = get_closest(territory, current_pos)
        else:
            rows = len(grid) if isinstance(grid, list) else 0
            cols = len(grid[0]) if grid and isinstance(grid[0], list) else 0
            target_pos = (rows // 2, cols // 2)

    delta_x = target_pos[0] - current_pos[0]
    delta_y = target_pos[1] - current_pos[1]

    dx = 0
    dy = 0
    if delta_x != 0:
        dx = 1 if delta_x > 0 else -1
    if delta_y != 0:
        dy = 1 if delta_y > 0 else -1

    def is_valid(x, y):
        if not grid or not isinstance(grid, list):
            return False
        if not (0 <= x < len(grid)):
            return False
        if not (0 <= y < len(grid[0])):
            return False
        return True

    new_x = current_pos[0] + dx
    new_y = current_pos[1] + dy
    if is_valid(new_x, new_y):
        if grid[new_x][new_y] == 0:
            return [dx, dy]
        else:
            for alt_dx, alt_dy in [(-dy, dx), (dy, -dx), (0, 0)]:
                alt_x = current_pos[0] + alt_dx
                alt_y = current_pos[1] + alt_dy
                if is_valid(alt_x, alt_y):
                    if grid[alt_x][alt_y] == 0:
                        return [alt_dx, alt_dy]
    return [0, 0]
