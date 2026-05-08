def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj8(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1])) == 1

    self_t = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2]

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    candidates = []
    if opp_t and unclaimed:
        for c in unclaimed:
            if any(adj8(c, ot) for ot in opp_t):
                candidates.append(c)
    if not candidates and opp_t:
        candidates = list(opp_t)
    if not candidates:
        candidates = unclaimed if unclaimed else list(self_t) if self_t else [(sx, sy)]
    targets = candidates

    # Pick a deterministic target
    best_target = None
    best_key = None
    for t in targets:
        if t in obstacles or not inb(t[0], t[1]):
            continue
        d1 = abs(t[0] - sx) + abs(t[1] - sy)
        d2 = abs(t[0] - ox) + abs(t[1] - oy)
        near = 1 if (opp_t and any(adj8(t, ot) for ot in opp_t)) else 0
        key = (-(near), d1, d2, t[0], t[1])
        if best_key is None or key < best_key:
            best_key = key
            best_target = t
    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    # Choose best move among 9 deltas
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist_to = abs(tx - nx) + abs(ty - ny)
        dist_to_now = abs(tx - sx) + abs(ty - sy)
        dist_opp = abs(ox - nx) + abs(oy - ny)
        enter_opp = 1 if (nx, ny) in opp_t else 0
        enter_opp_terr = enter_opp
        # Prefer faster approach, penalize getting too close to opponent, and seize opponent cells
        score = (-(enter_opp_terr * 1000), dist_to, -dist_opp, -((dist_to_now - dist_to) > 0), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]