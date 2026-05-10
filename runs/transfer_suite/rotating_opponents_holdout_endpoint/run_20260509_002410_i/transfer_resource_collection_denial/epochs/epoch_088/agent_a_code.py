def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    opp_block_margin = 0
    best_targets = []
    for r in resources:
        if not r or len(r) < 2:
            continue
        tx = int(r[0]); ty = int(r[1])
        if not (0 <= tx < w and 0 <= ty < h):
            continue
        us = md(sx, sy, tx, ty)
        op = md(ox, oy, tx, ty)
        # If opponent can reach strictly sooner, de-prioritize strongly
        if us <= op + opp_block_margin:
            score = (us - (op - us))  # smaller is better
            best_targets.append((score, tx, ty, us, op))
    if best_targets:
        best_targets.sort(key=lambda z: (z[0], z[1], z[2]))
        _, tx, ty, _, _ = best_targets[0]
    else:
        # Fall back to nearest resource
        best = None
        for r in resources:
            tx = int(r[0]); ty = int(r[1])
            if not (0 <= tx < w and 0 <= ty < h):
                continue
            us = md(sx, sy, tx, ty)
            cand = (us, tx, ty)
            if best is None or cand < best:
                best = cand
        _, tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Secondary target for determinism when equidistant: farthest-up-right among tied
    def tie_pref(nx, ny):
        return (-nx, -ny)

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_target = md(nx, ny, tx, ty)
        # Avoid moving into opponent's immediate neighborhood (resource_denier response)
        d_opp = md(nx, ny, ox, oy)
        opp_penalty = 2 if d_opp <= 1 else 0
        # Encourage staying closer to target and away from obstacles-adjacent traps
        trap = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                px, py = nx + ex, ny + ey
                if 0 <= px < w and 0 <= py < h and (px, py) in obstacles:
                    trap += 1
        key = (d_to_target + opp_penalty + trap * 0.01, tie_pref(nx, ny)[0], tie_pref(nx, ny)[1], dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]