def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_terr.add((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = w // 2, h // 2

    def manhattan(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_dx, best_dy = 0, 0
    best = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        in_opp = (nx, ny) in opp_terr
        in_un = (nx, ny) in unclaimed
        in_self = (nx, ny) in self_terr

        # Territory control: prefer flipping, then claiming unclaimed, then expanding away from opponent pressure.
        score = 0.0
        if in_opp:
            score += 6.0
        if in_un:
            score += 1.5
        if in_self:
            score += 0.2

        # Prefer moving closer to center (long-run territory).
        score += 0.3 * (-(manhattan(nx, ny, cx, cy)) + -(manhattan(sx, sy, cx, cy)))

        # Avoid giving the opponent immediate flip options: stay farther from opponent.
        score += 0.15 * (manhattan(nx, ny, ox, oy) - manhattan(sx, sy, ox, oy))

        # If we can flip, also prefer moves that reduce distance to the opponent to continue pressure.
        if in_opp:
            score += 0.25 * (manhattan(sx, sy, ox, oy) - manhattan(nx, ny, ox, oy))

        if score > best:
            best = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]