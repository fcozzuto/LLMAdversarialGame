def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escap" in role) or ("run" in role) or ("runner" in role)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x, y):
        ax = abs(x - ox)
        ay = abs(y - oy)
        return ax if ax > ay else ay

    def mobility(x, y):
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if inb(x + dx, y + dy):
                    cnt += 1
        return cnt

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    # Wall-running evasion: bias pursuer to avoid diagonals when near walls/obstacles, and bias evader to hug walls only if it preserves distance+mobility.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d = cheb(nx, ny)
        mob = mobility(nx, ny)

        near_wall = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
        opp_near_wall = (ox == 0 or ox == w - 1 or oy == 0 or oy == h - 1)

        # Count immediate obstacle pressure around the new position
        obs_cnt = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if not (0 <= tx < w and 0 <= ty < h):
                    obs_cnt += 1
                elif (tx, ty) in blocked:
                    obs_cnt += 1

        if is_evader:
            # Maximize survival: increase distance, keep high mobility, avoid getting boxed in (high obs_cnt), and if opponent is wall-focused, don't offer easy lines.
            # Deterministic tie-break: prefer lower obs_cnt, then higher mob, then smaller dx/dy lexicographic.
            score = (-d, obs_cnt, -mob, near_wall and opp_near_wall)
        else:
            # Pursuer: minimize distance; avoid getting funneled into walls (penalize near_wall when diagonal would reduce options), favor mobility.
            diag = (dx != 0 and dy != 0)
            wall_pen = 3 if (near_wall and (diag or opp_near_wall)) else 0
            score = (d, wall_pen + obs_cnt, -mob)

        if best is None or score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]