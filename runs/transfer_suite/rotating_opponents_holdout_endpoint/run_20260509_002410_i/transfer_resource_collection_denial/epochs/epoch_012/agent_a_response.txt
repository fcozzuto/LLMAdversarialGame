def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obstacle_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacle_set.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacle_set

    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    # local "danger" from obstacles: discourage stepping near walls/obstacles
    def obstacle_prox(x, y):
        cnt = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacle_set:
                    cnt += 1
        return cnt

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # choose next cell by maximizing "advantage" over opponent for best resource from that cell
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        prox_pen = 0.15 * obstacle_prox(nx, ny)
        # also slightly penalize moving away from both agents to reduce dithering
        base_keep = -0.01 * (manh(nx, ny, sx, sy) + manh(nx, ny, ox, oy))

        # compute best resource value reachable from (nx,ny)
        best_cell_val = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacle_set:
                continue
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)

            # Main: prioritize resources where we are closer than opponent.
            # Secondary: account for our travel time and competition tightness.
            # If we can "intercept" sooner (lower sd and larger od-sd), prioritize.
            adv = od - sd
            tight = -(sd * 0.03)  # prefer closer to reduce time-to-collect
            intercept = 0
            if adv > 0:
                intercept = 0.25 * adv
            # mild preference to go for nearer resources when adv is small/negative
            catchup = -0.08 * sd - 0.02 * (sd - od if od < sd else 0)

            val = intercept + tight + catchup + adv * 0.06 + base_keep - prox_pen
            if val > best_cell_val:
                best_cell_val = val

        # tie-break: if equal, prefer staying still
        if best_cell_val > best_val or (best_cell_val == best_val and (dx, dy) == (0, 0)):
            best_val = best_cell_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]