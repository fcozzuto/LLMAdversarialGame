def choose_move(observation):
    # Defensive extraction with sensible defaults
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)

    me = observation.get("self_position", {})
    if isinstance(me, dict):
        mx = me.get("x", 0)
        my = me.get("y", 0)
    else:
        mx = observation.get("self_x", 0)
        my = observation.get("self_y", 0)

    op = observation.get("opponent_position", {})
    if isinstance(op, dict):
        ox = op.get("x", mx)
        oy = op.get("y", my)
    else:
        ox = mx
        oy = my

    dx = 0
    dy = 0

    # If on same cell, move toward a corner to create space
    if mx == ox and my == oy:
        dx = 1 if mx < w - 1 else -1 if mx > 0 else 0
        dy = 1 if my < h - 1 else -1 if my > 0 else 0
        return [dx, dy]

    # Move toward opponent
    if mx < ox:
        dx = 1
    elif mx > ox:
        dx = -1

    if my < oy:
        dy = 1
    elif my > oy:
        dy = -1

    obstacles = observation.get("obstacles", [])
    def blocked(nx, ny):
        for ob in obstacles:
            bx = ob.get("x", -1)
            by = ob.get("y", -1)
            if nx == bx and ny == by:
                return True
        return False

    nx = mx + dx
    ny = my + dy
    if 0 <= nx < w and 0 <= ny < h and not blocked(nx, ny):
        return [dx, dy]

    if 0 <= mx < w and 0 <= my < h and not blocked(mx, my):
        return [0, 0]

    # Explore alternatives to avoid blocks
    if mx + 1 < w and not blocked(mx + 1, my):
        return [1, 0]
    if mx - 1 >= 0 and not blocked(mx - 1, my):
        return [-1, 0]
    if my + 1 < h and not blocked(mx, my + 1):
        return [0, 1]
    if my - 1 >= 0 and not blocked(mx, my - 1):
        return [0, -1]

    return [0, 0]
