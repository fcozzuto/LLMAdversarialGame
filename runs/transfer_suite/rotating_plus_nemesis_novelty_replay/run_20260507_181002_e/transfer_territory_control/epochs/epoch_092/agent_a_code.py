def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    resources = toset(observation.get("resources"))
    unclaimed = toset(observation.get("unclaimed_cells"))

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_score = -10**18

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        score = 0.0

        if resources:
            md = None
            for rx, ry in resources:
                d = dist2(nx, ny, rx, ry)
                if md is None or d < md:
                    md = d
            score += 500.0 / (1.0 + md)
        if unclaimed and (nx, ny) in unclaimed:
            score += 20.0

        # Prefer moves that reduce opponent influence when resources exist, else increase distance
        dpo = dist2(nx, ny, ox, oy)
        if resources:
            score += 30.0 / (1.0 + dpo)
        else:
            score -= dpo * 0.01

        # Small deterministic preference to avoid oscillation: stay if currently safe and not losing
        if dx == 0 and dy == 0:
            score += 1.0

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]