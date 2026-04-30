def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def king(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    me = (sx, sy)
    opp = (ox, oy)
    if not resources:
        return [0, 0]

    # Deterministic target selection: prioritize resources we are closer/equal to, then tie-break by coordinate.
    resources.sort()
    best_r = resources[0]
    best_val = -10**9
    for r in resources:
        myd = king(me, r)
        opd = king(opp, r)
        # Encourage securing contested resources and grabbing far-but-free resources if we are ahead.
        val = (opd - myd) * 10 - myd
        if myd <= opd:
            val += 20
        else:
            val -= 5 * (myd - opd)
        # Slight preference to avoid marching into opponent's vicinity.
        val -= 0.2 * king(opp, r)
        if val > best_val:
            best_val = val
            best_r = r

    tx, ty = best_r

    cand_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            cand_moves.append((dx, dy, nx, ny))

    # If somehow no legal moves, stay.
    if not cand_moves:
        return [0, 0]

    curd = king(me, best_r)
    oppd = king(opp, best_r)
    # Candidate evaluation: move toward target, avoid worsening distance, and slightly avoid giving opponent an advantage.
    best_move = (0, 0, -10**9)
    for dx, dy, nx, ny in cand_moves:
        md = king((nx, ny), best_r)
        # Prefer reductions in distance; allow ties with better "capture contest".
        contest = king((ox, oy), best_r)
        gain = (curd - md) * 12
        forward = -md * 2
        # Discourage stepping closer to opponent unless it also reduces our distance more.
        step_to_opp = king((nx, ny), opp)
        opp_adv = (king((ox, oy), best_r) - oppd)  # mostly 0, but deterministic
        # Primary objective + minor tie-breakers.
        score = gain + forward - 0.15 * step_to_opp - 0.1 * contest - 0.05 * opp_adv
        if score > best_move[2]:
            best_move = (dx, dy, score)

    return [int(best_move[0]), int(best_move[1])]