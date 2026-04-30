def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    rem = observation.get("remaining_resource_count", None)
    rem = int(rem) if rem is not None else len(resources)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (0, 0)
    best_val = -10**18

    if not resources:
        # No visible resources: maximize distance from opponent
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d_op = cheb(nx, ny, ox, oy)
            if d_op > best_val:
                best_val = d_op
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    urgency_avoid = rem <= 5
    urgency_seek = rem >= 7

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        # prefer closer to nearest resource
        d_res = min(cheb(nx, ny, rx, ry) for rx, ry in resources) if resources else 10**9
        # prefer staying away from opponent when resources are scarce
        d_op = cheb(nx, ny, ox, oy)
        val = -d_res
        if urgency_avoid:
            val += d_op * 0.6
        if urgency_seek:
            val += d_op * 0.1
        if (nx, ny) == (ox, oy):
            val -= 1000
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]