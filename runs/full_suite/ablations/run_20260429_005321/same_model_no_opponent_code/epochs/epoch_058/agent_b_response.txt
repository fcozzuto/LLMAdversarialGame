def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cands = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            cands.append((dx, dy))

    if not cands:
        return [0, 0]

    best = (0, 0)
    best_val = -10**18
    opp_d = dist(sx, sy, ox, oy)

    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy
        if dist(nx, ny, ox, oy) == 0:
            continue

        # resource race: want self to be closer than opponent for some resource
        if resources:
            val = 0
            for rx, ry in resources:
                sd = dist(nx, ny, rx, ry)
                od = dist(ox, oy, rx, ry)
                # lower (sd-od) is better; scale to favor decisive races
                race = (od - sd)
                if race > 0:
                    val += 30 * race - 2 * sd
                else:
                    val += race - sd

            # discourage moving adjacent to opponent if not winning a resource race
            near = dist(nx, ny, ox, oy) <= 1
            if near and opp_d > 2:
                val -= 25

            # encourage moving toward the closest resource when races are tied
            closest = min(dist(nx, ny, rx, ry) for rx, ry in resources)
            val += -2 * closest

            # obstacle avoidance implicit via candidates; slight center preference to reduce dithering
            cx, cy = w // 2, h // 2
            val += -0.2 * dist(nx, ny, cx, cy)

        else:
            # no resources: directly manage opponent distance
            val = -dist(nx, ny, ox, oy)
            if opp_d <= 3:
                val += 5  # keep pressure when close

        # deterministic tie-break: prefer move that ends farther from opponent if close; else prefer resource approach
        if val > best_val:
            best_val = val
            best = (dx, dy)
        elif val == best_val:
            if dist(nx, ny, ox, oy) > dist(sx + best[0], sy + best[1], ox, oy):
                best = (dx, dy)

    return [int(best[0]), int(best[1])]