def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx, cy
    else:
        # Choose a target resource deterministically, alternating emphasis by turn_index
        t = int(observation.get("turn_index", 0))
        flip = (t % 2 == 0)
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we're closer, prefer it strongly; otherwise prefer whichever we can reach relatively sooner.
            # Alternate between greedier and more "blocking/denying" selection.
            if flip:
                closer_bonus = -1000 if ds <= do else 0
                tie = 0 if ds == do else (do - ds)  # smaller gap is better when we are worse
                key = (closer_bonus + (ds * 10) + (0 if ds <= do else tie), rx, ry)
            else:
                # Deny: prefer resources the opponent is not closer to than us; if all are, prefer smallest (do - ds).
                deny = 0 if ds <= do else (do - ds)
                key = (deny * 100 + ds, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    # Candidate moves
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break changes with turn_index
    shift = int(observation.get("turn_index", 0)) % 9
    moves = moves[shift:] + moves[:shift]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        # Avoid stepping onto opponent (engine may block/resolve, but keep safe)
        if nx == ox and ny == oy:
            continue

        d_next = cheb(nx, ny, tx, ty)
        d_now = cheb(sx, sy, tx, ty)
        # Encourage progress; lightly discourage moving away; add small penalty for proximity to opponent to reduce interference
        dp = cheb(nx, ny, ox, oy)
        val = (d_next * 1000) + (0 if d_next <= d_now else (d_next - d_now) * 10) + (0 if dp > 0 else -1)
        # Also account for whether the move directly reaches a resource
        if (nx, ny) in set((p[0], p[1]) for p in resources):
            val -= 200000

        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]