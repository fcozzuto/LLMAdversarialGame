def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("evade" in role) or ("runner" in role) or ("escape" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def dist(x, y):
        return abs(x - ox) + abs(y - oy)
    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    def best_after(x, y):
        # Greedy 1-ply estimate: if evader, assume opponent minimizes distance; else assume opponent maximizes distance.
        # We only need our evaluation, not exact opponent move.
        d0 = dist(x, y)
        if d0 == 0:
            return -10**9 if is_evader else 10**9
        if is_evader:
            # avoid being cornered: prioritize distance, then mobility
            return d0 * 10 + mobility(x, y)
        else:
            # prioritize getting closer, then reduce opponent options (our mobility)
            return -d0 * 10 - mobility(x, y)

    # If pursuing, never step into positions that are immediate "bad" due to being forced back; if escaping, avoid low-mobility squares.
    best_move = [0, 0]
    best_val = -10**18 if not is_evader else -10**18
    if not is_evader:
        best_val = 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # 2-step lookahead for determinism and better obstacle handling
        # Our next position is (nx,ny). Evaluate our prospects under greedy response using only local mobility.
        # Secondary term biases towards reducing distance (pursuer) or increasing it (evader).
        d = dist(nx, ny)
        mob = mobility(nx, ny)
        val = best_after(nx, ny)
        # Add tie-breakers deterministically using coordinates
        val += (nx * 0.001 + ny * 0.000001)
        if is_evader:
            # maximize
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
        else:
            # minimize distance (equivalently maximize closeness); our best_after returns negative closeness penalty
            # Choose the move with minimal d first, then best_after.
            if d < dist(sx + best_move[0], sy + best_move[1]):
                best_move = [dx, dy]
            elif d == dist(sx + best_move[0], sy + best_move[1]) and val < best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]