def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Approximate time with Chebyshev distance (diagonals allowed), penalize obstacles locally by skipping blocked next step
    def t_to(x, y, px, py):
        return max(abs(x - px), abs(y - py))

    best = None
    best_score = -10**18
    for r in resources:
        if r is None or len(r) < 2:
            continue
        tx, ty = int(r[0]), int(r[1])
        if not inb(tx, ty) or (tx, ty) in obstacles:
            continue
        ts = t_to(tx, ty, sx, sy)
        to = t_to(tx, ty, ox, oy)
        # Favor resources where we arrive earlier; also consider remaining count to keep pressure toward finish
        score = (to - ts) * 100 - ts * 2
        if best is None or score > best_score or (score == best_score and (tx, ty) < best):
            best_score = score
            best = (tx, ty)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Choose move that minimizes distance to target; tie-break by deterministic preference toward increasing our advantage.
    curd = max(abs(tx - sx), abs(ty - sy))
    best_move = [0, 0]
    best_mscore = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = max(abs(tx - nx), abs(ty - ny))
        # if move doesn't improve, still allow but with penalty; prefer reducing nd and increasing arrival gap vs opponent
        ts_next = t_to(tx, ty, nx, ny)
        to_curr = t_to(tx, ty, ox, oy)
        mscore = (to_curr - ts_next) * 100 - nd * 3 - (1 if (dx == 0 and dy == 0) else 0) * 5
        # deterministic tie-break: lexicographically smallest move among equal scores
        if mscore > best_mscore or (mscore == best_mscore and [dx, dy] < best_move):
            best_mscore = mscore
            best_move = [dx, dy]

    # If no move was valid (shouldn't happen), stay
    if best_mscore == -10**18:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]