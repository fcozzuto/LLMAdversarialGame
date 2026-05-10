def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inside(x, y) and (x, y) not in obs

    resources = observation.get("resources") or []
    unclaimed = observation.get("unclaimed_cells") or []

    targets = []
    for c in resources:
        if isinstance(c, (list, tuple)) and len(c) == 2:
            targets.append((int(c[0]), int(c[1])))
    for c in unclaimed:
        if isinstance(c, (list, tuple)) and len(c) == 2:
            targets.append((int(c[0]), int(c[1])))

    moves = [(0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        score = 0
        if targets:
            md = 10**9
            for tx, ty in targets:
                d = abs(nx - tx) + abs(ny - ty)
                if d < md:
                    md = d
            score += 1000 - md
        else:
            score += abs(nx - ox) + abs(ny - oy)
        # small deterministic tiebreak
        score += (-dx * 7 + dy * 3)
        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is not None:
        return [best[1], best[2]]

    for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            return [dx, dy]
    return [0, 0]