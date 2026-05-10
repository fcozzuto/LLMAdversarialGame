def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    if ("evad" in self_role) or self_role == "evader":
        mode = "evade"
    elif ("purs" in self_role) or self_role == "pursuer":
        mode = "pursue"
    else:
        mode = "pursue" if (("evad" in opponent_role) or (opponent_role == "evader")) else "evade"

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return (dx*dx + dy*dy)
    deltas = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]

    # Deterministic tie-breaker order (already fixed by deltas)
    best_move = (0, 0)
    if mode == "evade":
        best_val = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            if (nx, ny) in obs:
                continue
            d = dist(nx, ny, ox, oy)
            # Prefer moves that also keep away from obstacles (light penalty)
            adj_block = 0
            for adx, ady in deltas:
                tx, ty = nx + adx, ny + ady
                if inb(tx, ty) and (tx, ty) in obs:
                    adj_block += 1
            val = d - 0.15 * adj_block
            # Mild bias to not oscillate: prefer staying on same x/y if near-equivalent
            if val > best_val + 1e-9:
                best_val = val
                best_move = (dx, dy)
    else:
        best_val = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            d = dist(nx, ny, ox, oy)
            # Pursue greedily; add penalty if move would be "stuck" next to obstacles
            adj_block = 0
            for adx, ady in deltas:
                tx, ty = nx + adx, ny + ady
                if inb(tx, ty) and (tx, ty) in obs:
                    adj_block += 1
            val = -d - 0.05 * adj_block
            if val > best_val + 1e-9:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]