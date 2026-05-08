def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = sorted(dirs, key=lambda t: (t[0], t[1]))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal_moves(px, py):
        out = []
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if valid(nx, ny):
                out.append((dx, dy, nx, ny))
        return out

    my_moves = legal_moves(sx, sy)
    opp_moves = legal_moves(ox, oy)

    # If roles are as expected: evader maximizes distance; pursuer minimizes.
    # Minimax depth-1 with deterministic tie-break: opponent takes best counter-move.
    best = None
    if not is_evader:
        best_score = 10**9
        for mdx, mdy, nx, ny in my_moves:
            worst_for_us = -1
            for odx, ody, ex, ey in opp_moves:
                d = cheb(nx, ny, ex, ey)
                if d > worst_for_us:
                    worst_for_us = d
            # We want small remaining distance after opponent maximizes it.
            score = worst_for_us
            if score < best_score:
                best_score = score
                best = (mdx, mdy)
            elif score == best_score and best is not None:
                if (mdx, mdy) < best:
                    best = (mdx, mdy)
    else:
        best_score = -1
        for mdx, mdy, nx, ny in my_moves:
            best_for_us = -1
            for odx, ody, ex, ey in opp_moves:
                # If we're evader, opponent likely pursues, so we approximate as minimizing distance.
                d = cheb(ex, ey, nx, ny)
                if d < best_for_us or best_for_us < 0:
                    best_for_us = d
                else:
                    if d < best_for_us:
                        best_for_us = d
            # We want large distance against pursuer best response (minimizer).
            score = best_for_us
            if score > best_score:
                best_score = score
                best = (mdx, mdy)
            elif score == best_score and best is not None:
                if (mdx, mdy) < best:
                    best = (mdx, mdy)

    if best is None:
        best = (0, 0)
    return [int(best[0]), int(best[1])]