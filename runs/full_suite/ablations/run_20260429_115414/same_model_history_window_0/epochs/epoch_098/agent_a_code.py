def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(a, b):
        return 0 <= a < w and 0 <= b < h

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_target():
        best = None
        bestv = None
        for rx, ry in resources:
            ds = dist(x, y, rx, ry)
            do = dist(ox, oy, rx, ry)
            v = ds - 0.9 * do + (0.05 * (rx + ry))
            if bestv is None or v < bestv:
                bestv = v
                best = (rx, ry)
        return best

    target = best_target()
    if target is None:
        return [0, 0]
    tx, ty = target

    def pick_step():
        # deterministic scoring of candidate moves
        bestm = (0, 0)
        bestscore = None
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d_t = dist(nx, ny, tx, ty)
            d_o = dist(nx, ny, ox, oy)
            # prefer closer to target, slight avoid opponent vicinity, prefer move that heads toward target
            score = d_t + 0.08 * d_o - 0.02 * (dx * (tx - x) + dy * (ty - y))
            if bestscore is None or score < bestscore:
                bestscore = score
                bestm = (dx, dy)
        return bestm

    dx, dy = pick_step()
    if dx == 0 and dy == 0:
        # try a fallback avoiding obstacles even if scores tie
        for cand in dirs:
            cdx, cdy = cand
            nx, ny = x + cdx, y + cdy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                dx, dy = cdx, cdy
                break
    return [int(dx), int(dy)]