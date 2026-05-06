def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))

    if not legal(sx, sy):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if legal(nx, ny):
                    return [dx, dy]
        return [0, 0]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        if targets:
            cand = None
            for tx, ty in targets:
                ds = abs(tx - nx) + abs(ty - ny)
                do = abs(tx - ox) + abs(ty - oy)
                same_row = 1 if ty == oy else 0
                same_col = 1 if tx == ox else 0
                # Prefer grabbing near-row/col aligned resources before opponent sweeps.
                # Also prefer states where opponent is relatively farther.
                val = (do - ds) * 4 + (-ds) + same_row * 2 + same_col * 1
                # Slight bias toward moving generally toward center to avoid corner stagnation.
                val += - (abs(3.5 - nx) + abs(3.5 - ny)) * 0.05
                if cand is None or val > cand[0] or (val == cand[0] and ds < cand[1]):
                    cand = (val, ds)
            score = cand[0] if cand else -10**9
        else:
            # No resources: move to reduce distance to opponent's row/col while safe.
            score = -(abs(ny - oy) + abs(nx - ox)) - (abs(nx - sx) + abs(ny - sy)) * 0.01

        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]