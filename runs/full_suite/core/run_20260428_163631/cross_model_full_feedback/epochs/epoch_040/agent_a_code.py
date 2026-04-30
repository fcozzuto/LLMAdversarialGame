def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))
        except:
            pass

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        # Consider only a few best candidates by our distance (deterministic, small)
        scored = []
        for r in resources:
            ds = man((sx, sy), r)
            do = man((ox, oy), r)
            scored.append((ds, do, r))
        scored.sort(key=lambda t: (t[0], t[1], t[2][0], t[2][1]))
        candidates = [t for t in scored[:4]]  # up to 4

        rem = int(observation.get("remaining_resource_count", len(resources)))
        w_opp = 1.6 if rem > 3 else 2.2
        w_dist = 0.15 if rem > 3 else 0.08

        best_move = None
        best_val = -10**18
        cx, cy = w // 2, h // 2

        for dx, dy, nx, ny in legal:
            val = 0
            # Tie-breaker nudges toward center slightly when values close
            val += -0.01 * man((nx, ny), (cx, cy))
            for ds, do, r in candidates:
                nds = man((nx, ny), r)
                # Prefer states where we are closer than opponent to key resources
                val += (do - nds) * w_opp - nds * w_dist
            # Small preference for not stepping onto opponent-adjacent when tied
            if man((nx, ny), (ox, oy)) <= 1:
                val -= 0.25
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        # No visible resources: move toward center while staying away from opponent
        cx, cy = w // 2, h // 2
        best_move = None
        best_val = -10**18
        for dx, dy, nx, ny in legal:
            val = -man((nx, ny), (cx, cy)) - 0.8 * man((nx, ny), (ox, oy))
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]