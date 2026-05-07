def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        x = y = None
        if isinstance(a, dict):
            if "x" in a and "y" in a:
                x, y = int(a["x"]), int(a["y"])
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        if x is not None and 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def parse_xy(v):
        if isinstance(v, dict) and "x" in v and "y" in v:
            return int(v["x"]), int(v["y"])
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return None

    resources = []
    for r in observation.get("resources") or []:
        p = parse_xy(r)
        if p is None:
            continue
        x, y = p
        if (x, y) not in obstacles and 0 <= x < w and 0 <= y < h:
            resources.append((x, y))

    def md(a, b):
        ax, ay = a; bx, by = b
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy  # Chebyshev metric for 8-direction

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Deterministic fallback: approach the nearest corner opposite to opponent direction
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda c: md((ox, oy), c))
        # Move towards the far corner relative to opponent by reflecting over center-ish
        target = (0 if sx < w / 2 else w - 1, 0 if sy < h / 2 else h - 1)
        tx, ty = (target[0], target[1])
    else:
        best = None
        # Prefer resources closer to us than opponent; otherwise, choose the resource that minimizes the opponent gap.
        for r in resources:
            dS = md((sx, sy), r)
            dO = md((ox, oy), r)
            gap = dO - dS
            # If we can reach at least as fast, strongly prefer; else discourage but still consider reachable race.
            score = (1000 if gap >= 0 else 0) + gap * 10 - dS
            # Small obstacle-aware nudge: penalize proximity to obstacles near our current tile
            score -= 0.5 * (1 if (sx + 1, sy) in obstacles or (sx - 1, sy) in obstacles or (sx, sy + 1) in obstacles or (sx, sy - 1) in obstacles else 0)
            if best is None or score > best[0]:
                best = (score, r)
        tx, ty = best[1]

    # Choose move that reduces distance to target, with tie-break avoiding obstacles (no invalid move checks needed).
    best_mv = [0, 0]
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = md((nx, ny), (tx, ty))
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < (best_mv[0], best_mv[1])):
            best_d = d
            best_mv = [dx, dy]
    return best_mv