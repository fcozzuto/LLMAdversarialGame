def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "pos" in r and r["pos"] is not None and len(r["pos"]) >= 2:
                resources.append((int(r["pos"][0]), int(r["pos"][1])))
            elif "x" in r and "y" in r and r["x"] is not None and r["y"] is not None:
                resources.append((int(r["x"]), int(r["y"])))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick resource where we're much closer than opponent (deterministic).
    target = resources[0]
    best_gap = -10**9
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        gap = d_op - d_me
        # Tie-break: prefer higher (d_op) then lower d_me then lexicographic.
        if gap > best_gap:
            best_gap = gap
            target = (rx, ry)
        elif gap == best_gap:
            d_me_t = cheb(sx, sy, target[0], target[1])
            d_op_t = cheb(ox, oy, target[0], target[1])
            if d_op > d_op_t or (d_op == d_op_t and (d_me < d_me_t or (d_me == d_me_t and (rx, ry) < target))):
                target = (rx, ry)

    tx, ty = target
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_new = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Go closer; also slightly discourage moves that let opponent be relatively closer to other nearby resources.
        near_pen = 0
        for rx, ry in resources:
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If opponent is close compared to us, penalize.
            if do - dm < best_gap:  # worse relative advantage than our chosen target
                near_pen += (best_gap - (do - dm))
        val = -d_new + 0.01 * d_opp - 0.001 * near_pen
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move