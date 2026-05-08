def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y):
                obs.add((x, y))

    res_set = set()
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y):
                res_set.add((x, y))

    if (sx, sy) in res_set:
        return [0, 0]

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (dx, dy) != (0, 0) and inb(nx, ny) and (nx, ny) not in obs:
                valid.append((dx, dy))
    valid.append((0, 0))

    def best_move(target_x, target_y, toward_res=True):
        best_key = None
        best = (0, 0)
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - target_x) + abs(ny - target_y)
            # Prefer closer; tie-break deterministically
            key = (d, 0 if toward_res else -1, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    if res_set:
        # Go toward nearest resource; deterministic tie-break by sorted order
        best_rx, best_ry = None, None
        best_d = None
        for rx, ry in sorted(res_set):
            d = abs(sx - rx) + abs(sy - ry)
            if best_d is None or d < best_d:
                best_d = d
                best_rx, best_ry = rx, ry
        return best_move(best_rx, best_ry, toward_res=True)

    # No resources: chase opponent
    return best_move(ox, oy, toward_res=False)