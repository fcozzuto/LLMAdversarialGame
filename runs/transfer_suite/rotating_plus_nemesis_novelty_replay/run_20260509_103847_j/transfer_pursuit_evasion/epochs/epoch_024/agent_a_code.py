def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    role = observation.get("self_role", "pursuer")
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h and (x, y) not in obs
    dist2 = lambda ax, ay, bx, by: (ax - bx) * (ax - bx) + (ay - by) * (ay - by)

    # Build legal moves for both agents from current positions
    def legal_moves(px, py):
        ms = []
        for dx, dy in deltas:
            nx, ny = px + dx, py + dy
            if inb(nx, ny):
                ms.append((dx, dy, nx, ny))
        return ms if ms else [(0, 0, px, py)]

    my_moves = legal_moves(sx, sy)
    opp_moves = legal_moves(ox, oy)

    # Minimax over a single step: opponent chooses a best response for them
    # pursuer wants small distance; evader wants large distance
    best = None
    best_val = None
    for dx, dy, nx, ny in my_moves:
        if role == "pursuer":
            # Opponent (evader) tries to maximize our distance.
            worst = -1
            for odx, ody, tox, toy in opp_moves:
                val = dist2(nx, ny, tox, toy)
                if val > worst:
                    worst = val
            score = -worst  # higher is better for us => maximize negative
        else:
            # Opponent (pursuer) tries to minimize our distance.
            bestd = 10**18
            for odx, ody, tox, toy in opp_moves:
                val = dist2(nx, ny, tox, toy)
                if val < bestd:
                    bestd = val
            score = bestd

        # Deterministic tie-break: prefer smaller (|dx|+|dy|), then lexicographic dx,dy
        tie = (abs(dx) + abs(dy), dx, dy)
        if best is None or score > best_val or (score == best_val and tie < best[0]):
            best_val = score
            best = (tie, (dx, dy))

    return [best[1][0], best[1][1]]