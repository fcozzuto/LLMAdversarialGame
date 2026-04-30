def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not deltas:
        return [0, 0]

    # Precompute some opponent distance to encourage contesting near-future areas
    opp_d = md(sx, sy, ox, oy)

    best = None
    best_dxdy = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # If opponent can grab something right now, contest it by prioritizing
        # resources where we are relatively closer (or at least not much farther).
        if resources:
            scored = []
            for rx, ry in resources:
                ds = md(nx, ny, rx, ry)
                do = md(ox, oy, rx, ry)
                # Lower is better: distance for self, plus a penalty if opponent is much closer.
                # Also slightly prefer resources that are farther from opponent to avoid races.
                rel = ds - 0.85 * do
                # Tie-break: prefer resources that are nearer overall to reduce risk.
                scored.append((rel, ds, -do, rx, ry))
            scored.sort()
            rel, ds, negdo, _, _ = scored[0]
        else:
            rel, ds, negdo = 0.0, 0, 0

        # Small safety term: avoid moving into very close proximity when resources are scarce.
        safety = 0
        dpo = md(nx, ny, ox, oy)
        if opp_d <= 3 or len(resources) <= 3:
            safety = -2 if dpo <= 1 else (-1 if dpo == 2 else 0)

        # Encourage progression toward resources while reducing opponent advantage.
        # If opponent is close, we weight contest more strongly.
        contest_w = 1.25 if opp_d <= 3 else 0.9
        val = (ds + contest_w * (rel)) + safety + (0.01 * (abs(dx) + abs(dy)))

        # Deterministic tie-break: smaller val, then prefer moves that reduce distance to opponent.
        key = (val, md(nx, ny, ox, oy), dx, dy)
        if best is None or key < best:
            best = key
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]