def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    role = observation.get("self_role", "pursuer")
    best_move = [0, 0]
    if role == "pursuer":
        best = -10**18
        vxo, vyo = sx - ox, sy - oy
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            if nx == ox and ny == oy:
                return [dx, dy]
            d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            # Prefer strictly decreasing distance; break ties by moving along the line to the evader; avoid standing.
            dot = dx * vxo + dy * vyo
            score = (-d2) * 1000 + dot
            if dx == 0 and dy == 0:
                score -= 0.1
            best_move = [dx, dy] if score > best else best_move
            best = max(best, score)
        return best_move
    else:  # evader
        best = -10**18
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        ax, ay = None, None
        # Deterministic "escape corner": farthest from pursuer
        bestc = -1
        for cx, cy in corners:
            d2 = (cx - ox) * (cx - ox) + (cy - oy) * (cy - oy)
            if d2 > bestc:
                bestc = d2
                ax, ay = cx, cy
        vxo, vyo = sx - ox, sy - oy
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            if nx == ox and ny == oy:
                # Don't allow immediate capture if avoidable
                score = -10**12 - ((nx - ax) ** 2 + (ny - ay) ** 2)
            else:
                d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
                # Prefer maximizing distance; also head toward escape corner; discourage staying; mild anti-alignment.
                to_corner = (ax - nx) * vxo + (ay - ny) * vyo
                align_pen = (dx * vxo + dy * vyo)
                score = d2 * 1000 + to_corner - abs(align_pen) * 10
                if dx == 0 and dy == 0:
                    score -= 5
            if score > best:
                best = score
                best_move = [dx, dy]
        return best_move