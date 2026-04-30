def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def best_for(posx, posy):
        if not resources:
            res_term = 0
        else:
            dmin = 10**9
            for rx, ry in resources:
                d = cheb(posx, posy, rx, ry)
                if d < dmin:
                    dmin = d
            res_term = -dmin
        opp_term = cheb(posx, posy, ox, oy)
        # Prefer moving onto a resource strongly (res_term already helps, add direct boost)
        on_res = 1 if resources and any(posx == rx and posy == ry for rx, ry in resources) else 0
        # Combine: maximize advantage by getting closer to resources and farther from opponent
        return (on_res * 1000) + res_term * 10 + opp_term

    best_dx, best_dy = 0, 0
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        score = best_for(nx, ny) - cheb(nx, ny, ox, oy) * 0.5
        # deterministic tie-break: prefer staying if equal, else prefer smaller dx then smaller dy
        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy
        elif score == best_score:
            if (dx, dy) == (0, 0):
                best_dx, best_dy = dx, dy
            else:
                if best_dx == best_dy == 0:
                    continue
                if dx < best_dx or (dx == best_dx and dy < best_dy):
                    best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]