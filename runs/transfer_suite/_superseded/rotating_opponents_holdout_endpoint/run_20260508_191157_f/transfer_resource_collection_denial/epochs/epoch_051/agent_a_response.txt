def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def best_resource(px, py):
        if not resources:
            return None
        best = None
        best_score = None
        for rx, ry in resources:
            sd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach earlier (advantage), then closer, then smaller coordinates.
            adv = od - sd
            center = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
            parity = (px + py + rx + ry) & 1
            score = (adv * 1000.0) + (-sd * 10.0) + (-parity * 0.5) + (-center * 0.01)
            if best_score is None or score > best_score or (score == best_score and (rx, ry) < best):
                best_score = score
                best = (rx, ry)
        return best

    best_move = (0, 0)
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            tr = best_resource(nx, ny)
            if tr is None:
                val = 0.0
            else:
                rx, ry = tr
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                adv = od - sd
                # Add a small bias to keep moving in the direction we last chose (via tie-break on position).
                center = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
                val = (adv * 1000.0) + (-sd * 10.0) + (-center * 0.01) + (-(dx == 0 and dy == 0) * 0.25)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
            elif val == best_val:
                if (dx, dy) < best_move:
                    best_move = (dx, dy)

    return [best_move[0], best_move[1]]