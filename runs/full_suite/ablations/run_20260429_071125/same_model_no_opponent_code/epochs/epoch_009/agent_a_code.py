def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {tuple(p) for p in observation.get("obstacles", [])}
    resources = [tuple(p) for p in observation.get("resources", [])]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def safe(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def obst_pen(nx, ny):
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                    p += 2
        return p

    best_move = (0, 0)
    best_val = -10**18
    any_safe = False

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not safe(nx, ny):
            continue
        any_safe = True

        d_op = cheb(nx, ny, ox, oy)
        sep_term = d_op  # keep some separation

        if resources:
            best_res = 10**9
            contest = -10**9
            for rx, ry in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_op_r = cheb(ox, oy, rx, ry)
                if d_me < best_res:
                    best_res = d_me
                # Prefer resources where we are closer than opponent (or becoming closer).
                c = (d_op_r - d_me) * 3 - d_me
                if c > contest:
                    contest = c
            val = contest + sep_term * 0.2 - obst_pen(nx, ny) * 0.5
        else:
            # No resources: move to maximize distance from opponent while avoiding obstacles
            val = sep_term * 2 - obst_pen(nx, ny) * 1.0

        # Small tie-breaker: prefer moving toward center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = -cheb(nx, ny, cx, cy) * 0.05
        val += center_bias

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    if not any_safe:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]