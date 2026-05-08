def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_t = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2]
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj8(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1])) == 1

    if opp_t:
        best_t = None
        best_v = -10**18
        candidates = list(opp_t)
    else:
        best_t = None
        best_v = -10**18
        candidates = unclaimed if unclaimed else list(self_t)

    for tx, ty in candidates:
        if not inb(tx, ty) or (tx, ty) in obstacles:
            continue
        d_our = abs(tx - sx) + abs(ty - sy)
        near_self = 1 if any(adj8((tx, ty), s) for s in self_t) else 0
        near_opp = 1 if any(adj8((tx, ty), o) for o in opp_t) else 0
        if (tx, ty) in opp_t:
            v = 140.0 - 0.25 * d_our + 5.0 * near_self + 2.0 * near_opp
        else:
            v = 22.0 + 12.0 * near_self + 6.0 * near_opp - 0.08 * d_our
        if v > best_v:
            best_v = v
            best_t = (tx, ty)

    tx, ty = best_t if best_t is not None else (sx, sy)
    best_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        man = abs(tx - nx) + abs(ty - ny)
        capture_bonus = 0.0
        if (nx, ny) in opp_t:
            capture_bonus = 60.0
        elif (nx, ny) in unclaimed:
            capture_bonus = 12.0
        elif (nx, ny) in self_t:
            capture_bonus = 2.0
        best_moves.append((man - capture_bonus, dx, dy))
    best_moves.sort()
    if best_moves:
        return [int(best_moves[0][1]), int(best_moves[0][2])]
    return [0, 0]