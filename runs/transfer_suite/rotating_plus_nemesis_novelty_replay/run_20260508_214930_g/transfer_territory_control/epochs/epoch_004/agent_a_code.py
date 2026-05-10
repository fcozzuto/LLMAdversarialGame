def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = set(tuple(p) for p in (observation.get("obstacles") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    un_t = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    my_t = set(tuple(p) for p in (observation.get("self_territory") or []))

    cx1, cy1 = 3, 3
    cx2, cy2 = 4, 4

    options = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 0), (0, 1),
               (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    neigh4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = 0

        if (nx, ny) in opp_t:
            score += 1000
        elif (nx, ny) in un_t:
            score += 320
            dcent = md(nx, ny, cx1, cy1)
            dcent2 = md(nx, ny, cx2, cy2)
            if dcent2 < dcent:
                dcent = dcent2
            score += max(0, 80 - 6 * dcent)

        # Encourage controlled frontier expansion
        adj_my = 0
        adj_opp = 0
        for ax, ay in neigh4:
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h:
                if (tx, ty) in my_t:
                    adj_my += 1
                if (tx, ty) in opp_t:
                    adj_opp += 1
        score += 60 * adj_my
        score += 35 * adj_opp

        # Mild keep-away from opponent to reduce flipping vulnerability
        d_opp = md(nx, ny, ox, oy)
        score -= 2 * (7 if d_opp >= 7 else d_opp)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move