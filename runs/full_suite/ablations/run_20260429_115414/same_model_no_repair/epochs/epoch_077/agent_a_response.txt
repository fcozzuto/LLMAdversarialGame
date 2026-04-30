def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((x, y) for x, y in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def dist_to_obstacles(x, y):
        best = 10**9
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
                if best == 0:
                    return 0
        return best if obstacles else 10

    def best_target():
        best_res = None
        best_val = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer targets we can reach earlier (or where we gain vs opponent)
            val = (do - ds) * 100
            # Secondary: prefer higher obstacle clearance along the destination and from current
            val += (dist_to_obstacles(sx, sy) - dist_to_obstacles(rx, ry)) * 2
            # Tie-break: slightly prefer closer to our current and toward mid to reduce pathing quirks
            val += -ds * 0.5
            val += -abs(rx - (w - 1) / 2) * 0.01 - abs(ry - (h - 1) / 2) * 0.01
            if val > best_val:
                best_val = val
                best_res = (rx, ry)
        return best_res

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    if resources:
        target = best_target()
        tx, ty = target
        best_move = (0, 0)
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            ns = cheb(nx, ny, tx, ty)
            nos = cheb(ox, oy, tx, ty)
            score = (nos - ns) * 100
            score += (dist_to_obstacles(sx, sy) - dist_to_obstacles(nx, ny)) * 2
            score += -ns * 0.5
            # Small deterministic tie-break using turn_index
            score += -0.001 * ((nx + 3 * ny + observation.get("turn_index", 0)) % 97)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        # No resources: drift toward center while avoiding obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_move = (0, 0)
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, cx, cy)
            score = -d * 10 + dist_to_obstacles(nx, ny)
            score += -0.001 * ((nx + 3 * ny + observation.get("turn_index", 0)) % 97)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]