def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obst = set(tuple(p) for p in observation.get("obstacles", []))
    rem = observation.get("remaining_resource_count", len(resources))
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def next_pos(dx, dy):
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            return nx, ny
        return None

    if resources and rem > 0:
        targets = [tuple(r) for r in resources if tuple(r) not in obst]
    else:
        targets = []

    best_dx, best_dy = 0, 0
    best_score = -10**18

    for dx, dy in dirs:
        np = next_pos(dx, dy)
        if np is None:
            continue
        x, y = np
        if targets:
            # Prefer moves that increase how much closer we are than opponent to the best remaining resource
            best_adv = -10**18
            for rx, ry in targets:
                d_s = abs(rx - x) + abs(ry - y)
                d_o = abs(rx - ox) + abs(ry - oy)
                adv = d_o - d_s
                if adv > best_adv:
                    best_adv = adv
            # Slightly prefer shorter distance to avoid dithering
            d_to_nearest = min(abs(rx - x) + abs(ry - y) for rx, ry in targets)
            score = best_adv * 1000 - d_to_nearest
        else:
            # If no resources, chase opponent
            score = -man((x, y), (ox, oy))
        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]