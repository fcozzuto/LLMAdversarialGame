def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    free = lambda x, y: inb(x, y) and (x, y) not in obstacles
    cheb = lambda x1, y1, x2, y2: max(abs(x1 - x2), abs(y1 - y2))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # Evaluate each move by best "contested" resource advantage after moving.
    # If we can arrive no later than opponent, we strongly favor it; otherwise we still
    # head toward resources where we reduce the opponent's lead.
    bestdxdy = [0, 0]
    bestv = -10**18
    turn = int(observation.get("turn_index", 0) or 0)
    for dx, dy, nx, ny in cand:
        # Small deterministic tie-break by direction
        tie = ((dx + 2 * dy + turn) % 7) * 0.001
        v = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Contest score: reward arriving earlier, penalize later.
            lead = d_op - d_me  # positive if we are closer in moves
            sc = 12 * lead - 1.3 * d_me
            # Extra: if opponent is already extremely close, prefer moves that reduce our distance a lot.
            if d_op <= 1:
                sc += 5 if lead > 0 else -4
            if sc > v:
                v = sc
        # If no resources, move to maximize distance from opponent (deterministic survival).
        if not resources:
            v = -cheb(nx, ny, ox, oy)

        # Mild anti-collision: don't move onto opponent position.
        if (nx, ny) == (ox, oy):
            v -= 50
        v += tie
        if v > bestv:
            bestv = v
            bestdxdy = [dx, dy]
    return bestdxdy