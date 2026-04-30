def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                resources.append((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs

    best_move = (0, 0)
    best_score = -10**18

    if resources:
        # Select action that improves our best available target while discouraging targets we can't reach first.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # Reward: closer to our nearest "valuable" resource, penalize if opponent is closer to that resource.
            score = 0
            for rx, ry in resources:
                d_self = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                # If opponent is already closer or equal, don't chase too hard.
                # Also slightly prefer reducing distance to nearer resources overall.
                score += 1200 / (1 + d_self) - 900 / (1 + d_opp)
                # Prefer staying away from opponent to reduce their capture efficiency.
                score += (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy)) * 3
            # Small deterministic preference: move ordering breaks ties consistently.
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        # No visible resources: move toward center, but avoid moving into obstacle-free direct lines is not modeled;
        # just drift toward center while increasing distance to opponent.
        cx, cy = (W - 1) // 2, (H - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            score = -cheb(nx, ny, cx, cy) + cheb(nx, ny, ox, oy)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]