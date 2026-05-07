def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_score = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer we arrive earlier; if tie, prefer bigger advantage to deny; stable deterministic tiebreak.
        score = (ds > 0 and ds * 1000) - do  # lower is better
        # Transform so smaller ds and larger (do-ds) improves
        score = (ds * 200) - (do - ds)
        tie = (rx + 17 * ry)  # deterministic
        key = (score, ds, -do, tie)
        if best is None or key < best_score:
            best = (rx, ry)
            best_score = key

    tx, ty = best

    # Candidate moves: prioritize greedy towards target, but avoid obstacle by choosing next best.
    greedy_dx = 0 if tx == sx else (1 if tx > sx else -1)
    greedy_dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                # score based on progress to target + deny bonus if next position can threaten quickly
                d_to = cheb(nx, ny, tx, ty)
                d_opp = cheb(ox, oy, tx, ty)
                moves.append(((d_to * 10) - (d_opp - d_to), -dx, -dy, dx, dy))
    if not moves:
        return [0, 0]

    # Ensure greedy move is preferred when valid
    gkey = None
    for item in moves:
        if item[3] == greedy_dx and item[4] == greedy_dy:
            gkey = item
            break
    if gkey is not None:
        # But if greedy is poor due to being blocked indirectly, still allow best move.
        pass

    moves.sort()
    return [moves[0][3], moves[0][4]]