def choose_move(observation):
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh:
                obstacles.add((x, y))

    resources = []
    for it in observation.get("resources") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target():
        if not resources:
            return None
        best = None
        best_key = None
        for (rx, ry) in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            key = (od - sd, -sd, -(rx + 31 * ry))  # deterministic tie-break
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    def try_step(tx, ty):
        dx = tx - sx
        if dx > 0: mx = 1
        elif dx < 0: mx = -1
        else: mx = 0
        dy = ty - sy
        if dy > 0: my = 1
        elif dy < 0: my = -1
        else: my = 0

        candidates = [(mx, my)]
        if mx != 0 and my != 0:
            candidates += [(mx, 0), (0, my), (mx, -my), (-mx, my)]
        elif mx == 0 and my != 0:
            candidates += [(-1 if sx > tx else 1 if sx < tx else 0, my), (0, my), (1 if sx < tx else -1 if sx > tx else 0, 0)]
        elif my == 0 and mx != 0:
            candidates += [(mx, 0), (mx, 1 if sy < ty else -1 if sy > ty else 0), (0, 1 if sy < ty else -1 if sy > ty else 0)]
        candidates += [(0, 0), (1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
        # Unique + clamp to {-1,0,1}
        seen = set()
        for cx, cy in candidates:
            if cx < -1 or cx > 1 or cy < -1 or cy > 1: 
                continue
            if (cx, cy) in seen: 
                continue
            seen.add((cx, cy))
            nx, ny = sx + cx, sy + cy
            if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles:
                return [int(cx), int(cy)]
        return [0, 0]

    target = best_target()
    if target is None:
        return [0, 0]
    return try_step(target[0], target[1])