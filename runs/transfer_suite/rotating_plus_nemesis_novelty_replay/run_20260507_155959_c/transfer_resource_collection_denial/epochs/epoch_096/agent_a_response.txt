def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (dx != 0 or dy != 0) and inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))
    moves.append((0, 0))
    if not moves:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If no resources, head toward far corner opposite opponent for long-term pressure.
    if not resources:
        tx = w - 1 if ox < w // 2 else 0
        ty = h - 1 if oy < h // 2 else 0
        best = min(moves, key=lambda m: md(sx + m[0], sy + m[1], tx, ty))
        return [int(best[0]), int(best[1])]

    # Choose a target resource where we are comparatively closer.
    # Tie-break by: (our_dist - opp_dist), then our_dist, then deterministic coord.
    best_t = None
    best_key = None
    for rx, ry in resources:
        d_self = md(sx, sy, rx, ry)
        d_opp = md(ox, oy, rx, ry)
        key = (d_self - d_opp, d_self, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    # Greedy step toward target with obstacle-aware lookahead (1-step penalty if it moves away).
    # Score move: progress toward target, plus avoid risky "stall" by biasing to reduce distance.
    best_m = (0, 0)
    best_score = None
    cur_d = md(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obs:
            continue
        nd = md(nx, ny, tx, ty)
        # Prefer moving closer; if equal, prefer closer to target and alignment (diagonal allowed).
        progress = cur_d - nd
        diag_bonus = -0.01 if (dx == 0 or dy == 0) else 0.0
        # Light deterrent from moving into dead-end near obstacles: discourage staying adjacent count high.
        adj_block = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obs:
                    adj_block += 1
        # Deterministic tie-break: favor lexicographically smaller move among equals.
        key = (-(progress), nd, adj_block, dx, dy)
        if best_score is None or key < best_score:
            best_score = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]