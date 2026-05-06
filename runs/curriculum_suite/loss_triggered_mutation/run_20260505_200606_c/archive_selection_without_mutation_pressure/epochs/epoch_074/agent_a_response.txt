def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles if p is not None and len(p) >= 2}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    # Two-phase target: deny resources the opponent is closest to, else collect nearest
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        score = 0.0
        # Prefer positions that are safe from obstacles locally and can deny
        local_pen = 0
        for ax, ay in moves:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) in obs:
                local_pen += 1
        score -= 0.3 * local_pen

        if resources:
            # For each resource, estimate whether we should deny it
            for rx, ry in resources:
                if (rx, ry) in obs:
                    continue
                d_our = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                d_opp_next = d_opp
                # If opponent is already closer, aim to reduce our distance to interfere
                if d_opp < d_our:
                    # Deny pressure: larger when opponent is close; also reward making ourselves closer
                    score += 2.5 * (8 - d_opp) - 1.6 * d_our
                else:
                    # If we can get it earlier, collect efficiently
                    score += 1.2 * (10 - d_our) - 0.4 * d_opp

            # Small preference for not moving away from "most contested" resources
            # (resource where opponent currently is closest)
            dmap = []
            for rx, ry in resources:
                if (rx, ry) in obs:
                    continue
                dmap.append((cheb(ox, oy, rx, ry), rx, ry))
            if dmap:
                dmin, rx, ry = min(dmap, key=lambda t: t[0])
                score += 0.8 * (dmin - cheb(nx, ny, rx, ry))
        else:
            score -= 999

        # Tie-break deterministically: closer to opponent's closest resource, then lexicographic move
        tie1 = cheb(nx, ny, resources[0][0], resources[0][1]) if resources else 0
        key = (-score, tie1, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best else [0, 0]