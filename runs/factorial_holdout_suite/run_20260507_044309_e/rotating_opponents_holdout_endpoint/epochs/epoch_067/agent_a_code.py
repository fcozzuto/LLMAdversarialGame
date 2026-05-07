def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    # Heuristic target selection:
    # Prefer resources where we are closer than opponent; break ties by smaller distance-to-self.
    # Add a small obstacle "drag" based on how many straight-line segments cross obstacles (approx).
    def line_drag(x0, y0, x1, y1):
        steps = max(abs(x1 - x0), abs(y1 - y0))
        if steps == 0:
            return 0
        cx, cy = x0, y0
        drag = 0
        for i in range(1, steps + 1):
            nx = x0 + (x1 - x0) * i / steps
            ny = y0 + (y1 - y0) * i / steps
            gx, gy = int(round(nx)), int(round(ny))
            if (gx, gy) in obstacles:
                drag += 1
        return drag

    best = None
    best_key = None
    for x, y in resources:
        sd = abs(x - sx) + abs(y - sy)
        od = abs(x - ox) + abs(y - oy)
        # If we can reach sooner, prioritize; if not, avoid unless all are worse.
        advantage = od - sd  # higher is better
        drag = line_drag(sx, sy, x, y)
        key = (-(1 if advantage >= 0 else 0), -advantage, sd + 0.5 * drag, x, y)
        # The first component makes any "we can arrive no later than opponent" preferred deterministically.
        if best_key is None or key < best_key:
            best_key, best = key, (x, y)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If diagonal path would step onto obstacle, try alternate deterministic direction.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Try axis moves in deterministic order that keeps progress towards target.
        options = []
        if dx != 0:
            options.append((dx, 0))
        if dy != 0:
            options.append((0, dy))
        if dx != 0 and dy != 0:
            options.append((dx, 0))
            options.append((0, dy))
        options.append((0, 0))
        for ddx, ddy in options:
            mx, my = sx + ddx, sy + ddy
            if 0 <= mx < w and 0 <= my < h and (mx, my) not in obstacles:
                return [int(ddx), int(ddy)]
        return [0, 0]

    # Keep within bounds deterministically (should be handled by engine but avoid invalid intent).
    nx, ny = sx + dx, sy + dy
    if not (0 <= nx < w and 0 <= ny < h):
        dx = 0 if not (0 <= sx + dx < w) else dx
        dy = 0 if not (0 <= sy + dy < h) else dy
    return [int(dx), int(dy)]