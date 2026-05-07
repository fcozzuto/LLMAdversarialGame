def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
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
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best_move = (0, 0)
    best_score = -10**9

    # Choose a contested-aware target: prefer resources where we are closer than opponent.
    targets = []
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        lead = d_opp - d_self  # positive means we are closer
        # Small quadrant bias to avoid drifting to same path as opponent.
        quad = (1 if (sx < w//2) == (rx < w//2) else 0) + (1 if (sy < h//2) == (ry < h//2) else 0)
        targets.append((lead, quad, rx, ry, d_self, d_opp))
    # Deterministic: sort by lead (desc), quad (desc), then nearest to us.
    targets.sort(key=lambda t: (-t[0], -t[1], t[4], t[2], t[3]))
    top_targets = targets[:min(5, len(targets))]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Evaluate by progress toward best target we are likely to secure.
        score = 0
        for lead, quad, rx, ry, d_self, d_opp in top_targets:
            d_self2 = cheb(nx, ny, rx, ry)
            d_opp2 = cheb(ox, oy, rx, ry)
            # Reward reducing distance; penalize moving toward a resource opponent can take sooner.
            score += (d_self - d_self2) * 10
            if d_self2 <= d_opp2:
                score += 25
            else:
                score -= (d_self2 - d_opp2) * 8
            # Encourage immediate collection if stepping onto resource.
            if (nx, ny) == (rx, ry):
                score += 120
            # Light repulsion from obstacles-adjacent states to avoid getting stuck.
            adj_obs = 0
            for ax, ay in [(1,0),(-1,0),(0,1),(0,-1)]:
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obstacles:
                    adj_obs += 1
            score -= adj_obs * 2
        # Tie-break: prefer moves that are closer to the primary target.
        primary = top_targets[0]
        px, py = primary[2], primary[3]
        score -= cheb(nx, ny, px, py)

        if score > best_score:
            best_score = score
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]