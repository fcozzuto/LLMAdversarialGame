def choose_move(observation):
    sx, sy = observation["self_position"]
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    cx, cy = w // 2 - 1, h // 2 - 1

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield nx, ny

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = (float("-inf"), None)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        is_self = (nx, ny) in self_t
        is_opp = (nx, ny) in opp_t
        is_un = (nx, ny) in unclaimed

        adj_opp = any((ax, ay) in opp_t for ax, ay in neigh8(nx, ny))
        adj_un = any((ax, ay) in unclaimed for ax, ay in neigh8(nx, ny))
        adj_self = any((ax, ay) in self_t for ax, ay in neigh8(nx, ny))
        adj_obs = any((ax, ay) in obstacles for ax, ay in neigh8(nx, ny))

        val = 0.0
        if is_opp:
            val += 4.5
        elif is_un:
            val += 2.5 + (2.0 if adj_opp else 0.0)
            val += 0.4 if adj_un else 0.0
        elif is_self:
            val += 0.3 + (0.8 if adj_opp else 0.0)
        else:
            val -= 0.5

        val += 0.2 if adj_self else 0.0
        val -= 0.15 * adj_obs
        val += -0.01 * (abs(nx - cx) + abs(ny - cy))  # slight center bias
        val += 0.03 if (dx, dy) != (0, 0) else 0.0  # prefer moving when not harming

        if val > best[0]:
            best = (val, [dx, dy])

    return best[1] if best[1] is not None else [0, 0]