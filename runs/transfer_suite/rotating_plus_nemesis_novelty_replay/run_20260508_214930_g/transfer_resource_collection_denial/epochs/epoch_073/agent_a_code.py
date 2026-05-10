def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    # Bias to stay on our "side" relative to opponent to counter row/line sweeps.
    t_rem = int(observation.get("turns_remaining", 0) or 0)
    urgency = 1 if t_rem <= 10 else 0

    want_x = 1 if sx < ox else -1
    want_y = 1 if sy < oy else -1

    best = None
    best_key = None
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)

        # Race: advantage in who reaches first; fallback: if late game, just minimize self distance.
        adv = od - sd
        # Side bias: prefer resources that are not "past" the opponent in x/y direction.
        side = (want_x * (tx - ox)) <= 0 and (want_y * (ty - oy)) <= 0
        side_bonus = -2 if side else 0

        # Deterministic tie-break: lexicographic order after scoring.
        # Use urgency to reduce brittleness: later game ignore opponent distance.
        score = (adv * (1 - urgency)) + (0 if urgency == 0 else -sd) + side_bonus
        key = (score, -sd, tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    def clamp(v, lo, hi):
        if v < lo: return lo
        if v > hi: return hi
        return v

    # Choose best immediate step toward target with obstacle check; deterministic tie-break by (dx,dy).
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
                nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
            if (nx, ny) in obstacles:
                continue
            d_to = man(nx, ny, tx, ty)
            # Small penalty for not improving to avoid stalling unless necessary.
            d_now = man(sx, sy, tx, ty)
            improve = d_now - d_to
            candidates.append(((improve, -d_to, dx, dy), [dx, dy]))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True, key=lambda z: z[0])
    return candidates[0][1]