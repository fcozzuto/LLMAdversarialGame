def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))
    # If no resources, just drift away from opponent while avoiding obstacles
    if not resources:
        best = (10**9, -10**9, 0, 0)
        for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d_opp = max(abs(nx - ox), abs(ny - oy))
            d_wall = min(nx, ny, w - 1 - nx, h - 1 - ny)
            key = (-d_wall, -d_opp)
            if (key[0], key[1], dx, dy) < (best[0], best[1], best[2], best[3]):
                best = (key[0], key[1], dx, dy)
        return [best[2], best[3]] if best[0] != 10**9 else [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Choose target resource that we are relatively closer to than the opponent
    best_res = None
    best_score = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        score = (do - ds) * 10 - ds
        if score > best_score:
            best_score = score
            best_res = (rx, ry)
        elif score == best_score and best_res is not None:
            if ds < dist((sx, sy), best_res) or (ds == dist((sx, sy), best_res) and do < dist((ox, oy), best_res)):
                best_res = (rx, ry)

    tx, ty = best_res
    # Greedy step toward target with obstacle avoidance; break ties by increasing distance from opponent
    candidates = []
    for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_t = dist((nx, ny), (tx, ty))
        d_o = dist((nx, ny), (ox, oy))
        on_target = 1 if (nx == tx and ny == ty) else 0
        candidates.append((d_t, -d_o, -on_target, dx, dy))
    candidates.sort()
    return [candidates[0][3], candidates[0][4]] if candidates else [0, 0]