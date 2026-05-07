def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    obs_set = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inb(px, py): obs_set.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs_set:
                resources.append((rx, ry))

    if not resources:
        tx, ty = (gw - 1) // 2, (gh - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # Pick resource where we have maximal "arrival advantage"; then closest to us.
    best_t = None
    best_key = None
    for tx, ty in resources:
        sd = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        key = (od - sd, -sd, - (tx + ty))  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t

    # Choose among legal deltas, avoiding obstacles; prefer moves that reduce (self - opp) distance gap.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): continue
        hit = (nx, ny) in obs_set
        sd2 = md(nx, ny, tx, ty)
        od2 = md(ox, oy, tx, ty)
        # Large penalty for obstacle; otherwise maximize advantage while minimizing our distance.
        score = (-(sd2 - od2), -sd2)
        if hit:
            score = (-10**9, -10**9)
        if best_score is None or score > best_score:
            best_score = score
            best_m = (dx, dy)

    if best_m is None:
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]
    return [int(best_m[0]), int(best_m[1])]