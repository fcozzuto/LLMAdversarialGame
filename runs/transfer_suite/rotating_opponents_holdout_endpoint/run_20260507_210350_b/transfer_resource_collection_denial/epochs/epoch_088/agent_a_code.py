def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def king_dist(ax, ay, bx, by):
        return max(abs(ax - bx), abs(ay - by))

    def one_step_dist(tx, ty, px, py):
        # best possible dist opponent/self can achieve in one king move
        best = king_dist(px, py, tx, ty)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = px + dx, py + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    d = king_dist(nx, ny, tx, ty)
                    if d < best:
                        best = d
        return best

    best_score = None
    best_t = None
    for rx, ry in resources:
        sd = king_dist(sx, sy, rx, ry)
        od = king_dist(ox, oy, rx, ry)
        opp_can_take_next = one_step_dist(rx, ry, ox, oy) <= sd  # contest risk
        # Prefer targets where we are closer, and where opponent is not catch-up-ready.
        score = (od - sd) * 2.0 - sd * 0.15
        if opp_can_take_next:
            score -= 4.0
        # Mild prefer toward board center to reduce edge traps (deterministic).
        center_bonus = 0.02 * (3.5 - abs(rx - 3.5)) + 0.02 * (3.5 - abs(ry - 3.5))
        score += center_bonus
        key = (score, -sd, rx, ry)
        if best_score is None or key > best_score:
            best_score = key
            best_t = (rx, ry)

    tx, ty = best_t

    best_move = None
    best_mkey = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            nd = king_dist(nx, ny, tx, ty)
            od = king_dist(ox, oy, tx, ty)
            # If multiple moves tie, prefer staying slightly safer: move that increases separation from opponent.
            sep = max(abs(nx - ox), abs(ny - oy))
            opp_next = one_step_dist(tx, ty, ox, oy)
            mkey = (-(nd), (od - nd), sep, -abs(dx) - abs(dy), dx, dy)
            if best_mkey is None or mkey > best_mkey:
                best_mkey = mkey
                best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]