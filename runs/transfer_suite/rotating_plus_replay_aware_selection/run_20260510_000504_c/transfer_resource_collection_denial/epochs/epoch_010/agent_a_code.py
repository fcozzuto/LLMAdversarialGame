def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def parse_resources():
        out = []
        for r in observation.get("resources", []) or []:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                out.append((int(r[0]), int(r[1])))
            elif isinstance(r, dict):
                pos = r.get("position", None)
                if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                    out.append((int(pos[0]), int(pos[1])))
                elif "x" in r and "y" in r:
                    out.append((int(r["x"]), int(r["y"])))
        return out

    resources = [p for p in parse_resources() if p not in obstacles]
    dxdy = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def clamp_move(x, y):
        if x < 0: x = 0
        if x >= w: x = w - 1
        if y < 0: y = 0
        if y >= h: y = h - 1
        return x, y

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # With no visible resources, move to contest: head toward opponent if close, else toward farthest safe corner
        moves = []
        for dx, dy in dxdy:
            nx, ny = clamp_move(sx + dx, sy + dy)
            if (nx, ny) in obstacles:
                continue
            dist_self_opp = cheb(nx, ny, ox, oy)
            dist_opp_to_us = cheb(ox, oy, nx, ny)
            score = (dist_opp_to_us - dist_self_opp) - 0.01 * (nx + ny)
            moves.append((score, [dx, dy]))
        moves.sort(key=lambda t: t[0], reverse=True)
        return moves[0][1] if moves else [0, 0]

    # Choose best next move by evaluating how it changes distance to the best target (self speed vs opponent speed)
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dxdy:
        nx, ny = clamp_move(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        # If move immediately grabs a resource, strongly prefer it
        immediate = 1 if (nx, ny) in resources else 0
        val = 0
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer targets we can reach sooner than opponent; also prefer overall closeness
            val += (10 - ds) * (1.0 + 0.2 * immediate) + 2.2 * (do - ds)
            # Small penalty for being far from the target set
            if ds == 0:
                val += 20
        # Normalize by count to keep scale stable
        val /= max(1, len(resources))
        # Secondary tie-break: reduce distance to opponent slightly (prevents gifting paths)
        val -= 0.02 * cheb(nx, ny, ox, oy)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move