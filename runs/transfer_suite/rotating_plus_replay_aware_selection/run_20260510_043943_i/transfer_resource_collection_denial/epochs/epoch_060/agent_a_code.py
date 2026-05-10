def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    # Precompute resource attractiveness for each side
    # Heuristic: prefer resources we reach sooner and that opponent reaches later.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy

        # If we can immediately secure a resource, do it.
        immediate = 0
        total = 0
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # base: deny opponent and advance our pickup
            val = (od - sd) * 120 - sd

            # stronger push for very close targets
            if sd == 0:
                val += 10**6
                immediate = 1
            elif sd == 1:
                val += 240
            elif sd == 2:
                val += 90

            # if opponent is extremely close to a resource we are not, try to "steal" it
            if od <= 1 and sd > od:
                val -= 260

            # slight tie-break toward central/upper-left bias for determinism
            val += ((rx * 3 + ry * 5 + sd) & 1) * 7

            total += val

        # If immediate pickup exists, it dominates.
        if immediate:
            score = 10**9 + total
        else:
            score = total

        # Prefer progress toward the best-denied resource (secondary)
        if not immediate:
            # compute our closest and opponent closest resource distances
            sdmin = 10**9
            odmin = 10**9
            for rx, ry in resources:
                d1 = man(nx, ny, rx, ry)
                d2 = man(ox, oy, rx, ry)
                if d1 < sdmin:
                    sdmin = d1
                if d2 < odmin:
                    odmin = d2
            score += (odmin - sdmin) * 18 - sdmin * 2

        if score > best_val:
            best_val = score
            best_move = [dx if cell_ok(sx + dx, sy + dy) else 0, dy if cell_ok(sx + dx, sy + dy) else 0]

    # Ensure returned move is a valid delta in {-1,0,1}
    if best_move[0] < -1 or best_move[0] > 1 or best_move[1] < -1 or best_move[1] > 1:
        return [0, 0]
    if not cell_ok(sx + best_move[0], sy + best_move[1]):
        return [0, 0]
    return best_move