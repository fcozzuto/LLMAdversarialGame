def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def neigh_cells(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield nx, ny

    def closest_to(targets):
        if not targets:
            return None
        return min(targets, key=lambda t: max(abs(t[0] - sx), abs(t[1] - sy)))

    frontier = [c for c in unclaimed if any(n in self_t for n in neigh_cells(c[0], c[1]))]
    if frontier:
        target = closest_to(frontier)
        prefer_opp = False
    else:
        attack = [c for c in opp_t if any(n in self_t for n in neigh_cells(c[0], c[1]))] or list(opp_t)
        target = closest_to(attack) if attack else None
        prefer_opp = True if attack else False

    if target is None:
        return [0, 0]

    tx, ty = target
    best = (0, 0)
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dist = max(abs(tx - nx), abs(ty - ny))
        moved = 1 if (dx or dy) else 0
        n_self = sum((p in self_t) for p in neigh_cells(nx, ny))
        n_opp = sum((p in opp_t) for p in neigh_cells(nx, ny))
        n_un = sum((p in unclaimed) for p in neigh_cells(nx, ny))
        gain = (6 if (nx, ny) in opp_t else 1) + 2 * n_self + 0.5 * n_un - 1.5 * n_opp
        if prefer_opp and (nx, ny) not in opp_t:
            gain -= 0.75
        key = (dist, -gain, -moved, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]