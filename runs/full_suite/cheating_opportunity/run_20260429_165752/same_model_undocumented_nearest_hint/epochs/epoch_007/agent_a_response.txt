def choose_move(observation):
    W = observation.get("grid_width", 8) or 8
    H = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    rem = int(observation.get("remaining_resource_count", 0) or 0)
    endgame = 1 if rem <= 4 else 0

    best_move = None
    best_val = -10**30
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        opp_d_next = man(nx, ny, ox, oy)
        # Prefer staying a bit away from opponent while still pushing for resources.
        defense = -0.15 * opp_d_next

        if not resources:
            val = defense
        else:
            val = defense
            # Evaluate move by the single best resource it improves for us.
            best_res = -10**30
            for rx, ry in resources:
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                # Advantage: we want larger (od - sd). In endgame, chase harder.
                adv = od - sd
                # If opponent is already much closer, devalue but keep possibility if endgame.
                penalty = 0
                if adv < 0:
                    penalty = (-adv) * (2.6 if endgame else 3.0)
                tie = -0.02 * sd
                # Slight preference to resources that aren't "behind" the opponent relative to us.
                along = (rx - sx) * (ox - sx) + (ry - sy) * (oy - sy)
                pos_bias = 0.0 if along <= 0 else (0.12 if endgame else 0.06)
                res_score = (5.2 if endgame else 4.0) * adv - sd + tie - penalty + pos_bias
                if res_score > best_res:
                    best_res = res_score
            # Also discourage moves that worsen our best achievable distance too much.
            val += best_res
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]